#!/bin/bash
echo "Copying new ezgif frame sequence..."
rm -rf frontend/public/sequences/trident/*.jpg

# The frames in assets/frame are named ezgif-frame-001.jpg to ezgif-frame-200.jpg
# We will copy them directly to frontend/public/sequences/trident/
# and rename them to 0001.jpg ... 0200.jpg for the SequencePlayer

for i in $(seq 1 200); do
  src=$(printf "assets/frame/ezgif-frame-%03d.jpg" $i)
  dst=$(printf "frontend/public/sequences/trident/%04d.jpg" $i)
  
  if [ -f "$src" ]; then
    cp "$src" "$dst" &
  else
    echo "Warning: $src not found"
  fi
  
  if (( i % 32 == 0 )); then wait; fi
done
wait

echo "Sequence copy complete! Total frames: $(ls -l frontend/public/sequences/trident/*.jpg | wc -l)"
