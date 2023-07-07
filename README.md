# Fill Certificate

## Script to batch fill certificates

### How does it work?
The script iterates through `data/timesheet.csv` and fills the value in the certificate template picked from `./certificate-template.jpg` and stores them in `certs/`. 
Each certificate is stored with name of the participant.

__Example:__

Certificate for Ashok Kumar would be stored in `certs/ashok_kumar.jpg`.

### How to use
* Go to config.ini and update the other sections to match the headers in the timesheet. See example below
* Where width is not provided, script will automatically center the text.
* Where left or right offset is provided, text will be offset accordingly. Offset doesn't work when width is explicitly given.
* Width and font size are required fields.
* Pass optional parameter --datafile to give path of your required datafile. It should be in csv format with header field.
* Pass optional parameter --outputpath to give alternate output directory
* Pass optional parameter --certificatefile to give path to the certificate file.
__Example:__
timesheet.csv
```
name,distance,time
Ashok Kumar, 5 km, "2:00:00"
```
config.ini
```
[image]
height=111
width=111
[name]
height=010
width_offset_left=000
width_offset_right=010
font_size=40
[distance]
width=040
height=030
font_size=20
[time]
width=080
height=030
font_size=20
```

### References
* Font: https://www.wfonts.com/search?kwd=serif
* Code: https://stackoverflow.com/questions/16373425/add-text-on-image-using-pil
* Docs: https://pillow.readthedocs.io/en/stable/reference/Image.html
* Similar project: https://crondev.blog/2014/06/16/make-a-certificate-creator-using-python/
