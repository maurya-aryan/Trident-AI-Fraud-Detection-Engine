#!/bin/bash
echo "Starting asset compilation..."
rm -rf frontend/public/sequences/trident/*.jpg

# Scene 1: 1 to 192 -> 0001.jpg to 0192.jpg
for i in $(seq 1 192); do
  src=$(printf "assets/scene1/%05d.png" $i)
  dst=$(printf "frontend/public/sequences/trident/%04d.jpg" $i)
  convert "$src" -quality 75 "$dst" &
  if (( i % 32 == 0 )); then wait; fi
done
wait

# Scene 2: 1 to 192 -> 0193.jpg to 0384.jpg
for i in $(seq 1 192); do
  src=$(printf "assets/scene2/%05d.png" $i)
  offset=$((i + 192))
  dst=$(printf "frontend/public/sequences/trident/%04d.jpg" $offset)
  convert "$src" -quality 75 "$dst" &
  if (( i % 32 == 0 )); then wait; fi
done
wait

# Scene 3: 1 to 60 -> 0385.jpg to 0444.jpg
for i in $(seq 1 60); do
  src=$(printf "assets/scene3/%05d.png" $i)
  offset=$((i + 384))
  dst=$(printf "frontend/public/sequences/trident/%04d.jpg" $offset)
  convert "$src" -quality 75 "$dst" &
  if (( i % 32 == 0 )); then wait; fi
done
wait
echo "Asset pipeline complete! Total frames: $(ls -l frontend/public/sequences/trident/*.jpg | wc -l)"
