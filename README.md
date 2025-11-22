```
ffmpeg -i C:\Users\Admin\Desktop\mfa-nepali\record.wav -ac 1 -ar 16000 -sample_fmt s16 C:\Users\Admin\Desktop\mfa-nepali\record_1.wav 
```

```
docker run -it --rm -v C:\Users\Admin\Desktop\mfa-nepali:/data mmcauliffe/montreal-forced-aligner:latest mfa align /data /data/Nepali_Dict.dict /data/Nepali_Acoustic_Model.zip /data/output  --output_format json
```
