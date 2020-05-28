Music Recombiner separates input music file into different stems. User can then select which stem and which part of music to augment. End result is recombined and the overall effect is a modified music file by the user.

Work is still in progress.

## Working
1. User uploads an .mp3 file.
2. Music Separator separates music into different stems.
3. User can then edit parts of song according to defined commands.
4. Re-combine the music.

## Add new command
1. Python
    1. Add logic in [augment.py](separator/main/augment/augment.py)
    2. Add tests in [test_augment.py](tests/test_augment.py)
    3. Add Table in [models.py](separator/models.py)
    4. Add function `store_{cmd_name}_attr` in [cmd_utils.py](separator/main/cmd_utils.py)
    5. Add mapping of command name -> function name in [cmd_utils.py](separator/main/cmd_utils.py)
2. HTML/JS
    1. Add input form for command in [augment.html](separator/templates/augment.html)
    2. Create a class in [script.js](separator/static/script.js)

# Screenshot

![Example](img/mr_login.png "Login Page")
![Example](img/mr_augment_page.png "Augment Page")
![Example](img/mr_no_augmentations.png "No Augmentations Modal")
![Example](img/mr_augmentations.png "Augmentations Modal")
