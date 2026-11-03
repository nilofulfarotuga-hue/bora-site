#!/bin/bash
# uso: montar_video2.sh CLIP.mp4 PASTA_PECAS CARTAZ_STORY.jpg SAIDA.mp4 [DUR_MONTAGEM]
set -e
CLIP="$1"; P="$2"; POST="$3"; OUT="$4"; DM="${5:-6.3}"
DUR=$(ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=p=0 "$CLIP")
SPEED=$(python3 -c "print($DUR/$DM)")
HOLD=$(python3 -c "print(10.0-$DM+0.3)")
FO=$(python3 -c "print($DM+0.05)")
TMP="${OUT%.mp4}.tmp.mp4"
ffmpeg -y -hide_banner -loglevel error \
 -i "$CLIP" \
 -framerate 30 -i "$POST" \
 -i "$P/v_mask2.png" \
 -framerate 30 -i "$P/v_cover.png" \
 -framerate 30 -i "$P/v_topstrip.png" \
 -f lavfi -t 10 -i anullsrc=r=48000:cl=stereo \
 -filter_complex "
 [0:v]reverse,setpts=PTS/$SPEED,fps=30,scale=988:524,format=rgba,tpad=stop_mode=clone:stop_duration=$HOLD,trim=duration=10,setpts=PTS-STARTPTS[vid];
 [2:v]format=gray,loop=-1:1,trim=duration=10,fps=30,setpts=PTS-STARTPTS[msk];
 [vid][msk]alphamerge,fade=t=out:st=$FO:d=0.6:alpha=1[band];
 [1:v]scale=1080:1920,format=rgba,loop=-1:1,trim=duration=10,setpts=PTS-STARTPTS[bg];
 [3:v]format=rgba,loop=-1:1,trim=duration=10,setpts=PTS-STARTPTS,fade=t=out:st=4.5:d=0.7:alpha=1[cov];
 [4:v]format=rgba,loop=-1:1,trim=duration=10,setpts=PTS-STARTPTS,fade=t=out:st=$FO:d=0.6:alpha=1[top];
 [bg][band]overlay=46:562[a0];
 [a0][top]overlay=46:554[a1];
 [a1][cov]overlay=0:1080,format=yuv420p,scale=1188:2112,zoompan=z='1+0.00016*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1080x1920:fps=30,setsar=1,format=yuv420p[v]" \
 -map "[v]" -map 5:a -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -r 30 -c:a aac -b:a 96k -t 10 -movflags +faststart "$TMP"
mv "$TMP" "$OUT"
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact "$OUT"
