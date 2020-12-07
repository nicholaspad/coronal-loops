ffmpeg -y -r 60 -start_number 0 -i aia171-images/%05d.png -vframes 1920 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/pre/aia171.mp4 \
&& ffmpeg -y -r 60 -start_number 0 -i aia304-images/%05d.png -vframes 1920 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/pre/aia304.mp4 \
&& ffmpeg -y -r 60 -start_number 0 -i hmi-images/%05d.png -vframes 1920 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/pre/hmi.mp4 \
&& ffmpeg -y -r 240 -start_number 1921 -i aia171-images/%05d.png -vframes 1450 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-in/aia171.mp4 \
&& ffmpeg -y -r 240 -start_number 1921 -i aia304-images/%05d.png -vframes 1450 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-in/aia304.mp4 \
&& ffmpeg -y -r 240 -start_number 1921 -i hmi-images/%05d.png -vframes 1450 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-in/hmi.mp4 \
&& ffmpeg -y -r 80 -start_number 3372 -i aia171-images/%05d.png -vframes 600 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-rmask/aia171.mp4 \
&& ffmpeg -y -r 80 -start_number 3372 -i aia304-images/%05d.png -vframes 600 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-rmask/aia304.mp4 \
&& ffmpeg -y -r 80 -start_number 3372 -i hmi-images/%05d.png -vframes 600 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-rmask/hmi.mp4 \
&& ffmpeg -y -r 40 -start_number 3973 -i aia171-images/%05d.png -vframes 218 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-emask/aia171.mp4 \
&& ffmpeg -y -r 40 -start_number 3973 -i aia304-images/%05d.png -vframes 218 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-emask/aia304.mp4 \
&& ffmpeg -y -r 40 -start_number 3973 -i hmi-images/%05d.png -vframes 218 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-emask/hmi.mp4 \
&& ffmpeg -y -r 240 -start_number 4192 -i aia171-images/%05d.png -vframes 2513 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-cmask/aia171.mp4 \
&& ffmpeg -y -r 240 -start_number 4192 -i aia304-images/%05d.png -vframes 2513 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-cmask/aia304.mp4 \
&& ffmpeg -y -r 240 -start_number 4192 -i hmi-images/%05d.png -vframes 2513 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/aia304-cmask/hmi.mp4 \
&& ffmpeg -y -r 25 -start_number 6706 -i aia171-images/%05d.png -vframes 125 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-rmask/aia171.mp4 \
&& ffmpeg -y -r 25 -start_number 6706 -i aia304-images/%05d.png -vframes 125 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-rmask/aia304.mp4 \
&& ffmpeg -y -r 25 -start_number 6706 -i hmi-images/%05d.png -vframes 125 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-rmask/hmi.mp4 \
&& ffmpeg -y -r 40 -start_number 6832 -i aia171-images/%05d.png -vframes 174 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-emask/aia171.mp4 \
&& ffmpeg -y -r 40 -start_number 6832 -i aia304-images/%05d.png -vframes 174 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-emask/aia304.mp4 \
&& ffmpeg -y -r 40 -start_number 6832 -i hmi-images/%05d.png -vframes 174 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-emask/hmi.mp4 \
&& ffmpeg -y -r 480 -start_number 7007 -i aia171-images/%05d.png -vframes 3515 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-cmask/aia171.mp4 \
&& ffmpeg -y -r 480 -start_number 7007 -i aia304-images/%05d.png -vframes 3515 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-cmask/aia304.mp4 \
&& ffmpeg -y -r 480 -start_number 7007 -i hmi-images/%05d.png -vframes 3515 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/hmi-cmask/hmi.mp4 \
&& ffmpeg -y -r 15 -start_number 10523 -i aia171-images/%05d.png -vframes 119 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/flare/aia171.mp4 \
&& ffmpeg -y -r 15 -start_number 10523 -i aia304-images/%05d.png -vframes 119 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/flare/aia304.mp4 \
&& ffmpeg -y -r 15 -start_number 10523 -i hmi-images/%05d.png -vframes 119 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/flare/hmi.mp4 \
&& ffmpeg -y -r 240 -start_number 10643 -i aia171-images/%05d.png -vframes 1424 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-out/aia171.mp4 \
&& ffmpeg -y -r 240 -start_number 10643 -i aia304-images/%05d.png -vframes 1424 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-out/aia304.mp4 \
&& ffmpeg -y -r 240 -start_number 10643 -i hmi-images/%05d.png -vframes 1424 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/zoom-out/hmi.mp4 \
&& ffmpeg -y -r 30 -start_number 12068 -i aia171-images/%05d.png -vframes 320 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/post/aia171.mp4 \
&& ffmpeg -y -r 30 -start_number 12068 -i aia304-images/%05d.png -vframes 320 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/post/aia304.mp4 \
&& ffmpeg -y -r 30 -start_number 12068 -i hmi-images/%05d.png -vframes 320 -vf scale=1024:1024 -q:v 2 -vcodec mpeg4 -b:v 800k raw-videos/post/hmi.mp4 \
&& ffmpeg -i raw-videos/pre/aia304.mp4 -i raw-videos/pre/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/pre/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/1.mp4 \
&& ffmpeg -i raw-videos/zoom-in/aia304.mp4 -i raw-videos/zoom-in/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/zoom-in/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/2.mp4 \
&& ffmpeg -i raw-videos/aia304-rmask/aia304.mp4 -i raw-videos/aia304-rmask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/aia304-rmask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/3.mp4 \
&& ffmpeg -i raw-videos/aia304-emask/aia304.mp4 -i raw-videos/aia304-emask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/aia304-emask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/4.mp4 \
&& ffmpeg -i raw-videos/aia304-cmask/aia304.mp4 -i raw-videos/aia304-cmask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/aia304-cmask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/5.mp4 \
&& ffmpeg -i raw-videos/hmi-rmask/aia304.mp4 -i raw-videos/hmi-rmask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/hmi-rmask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/6.mp4 \
&& ffmpeg -i raw-videos/hmi-emask/aia304.mp4 -i raw-videos/hmi-emask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/hmi-emask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/7.mp4 \
&& ffmpeg -i raw-videos/hmi-cmask/aia304.mp4 -i raw-videos/hmi-cmask/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/hmi-cmask/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/8.mp4 \
&& ffmpeg -i raw-videos/flare/aia304.mp4 -i raw-videos/flare/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/flare/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/9.mp4 \
&& ffmpeg -i raw-videos/zoom-out/aia304.mp4 -i raw-videos/zoom-out/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/zoom-out/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/10.mp4 \
&& ffmpeg -i raw-videos/post/aia304.mp4 -i raw-videos/post/aia171.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp1.mp4 \
&& ffmpeg -i temp1.mp4 -i raw-videos/post/hmi.mp4 -filter_complex '[0:v]pad=iw*2:ih[int];[int][1:v]overlay=W/2:0[vid]' -map [vid] -c:v libx264 -crf 23 -preset veryfast temp2.mp4 \
&& ffmpeg -y -i temp2.mp4 -filter:v "crop=3072:1024:0:0" output.mp4 \
&& rm temp1.mp4 \
&& rm temp2.mp4 \
&& mv output.mp4 ordered-videos/11.mp4 \
