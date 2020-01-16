# How it works?
Following these steps will allow you to run the application...

#### 1. Run server
Run orchestrators, factories and Ice services with `$ ./run_server`.

#### 2. Configure nodes
- First, open _IceGrid_ GUI with `$ icegridgui`. 
- Then, load _YoutubeDownloaderApp.xml_ template and log in into _IceGrid Registry_ (no password is needed). 
- Before that, **save the template to registry** and apply **patch distribution**.
- Finally, start de servers node by node.

#### 3. Run client
Edit `FILE_URL` and `FILE_NAME` variables in the script and execute `./run_client`.
This script will execute the following operations:
- Download the video from its URL (_$FILE_URL_).
- Show the current list of available files.
- Transfer the file by using its name (_$FILE_NAME_)

#### Packages needed...
- _Ice 3.7.0_
- _youtube-dl_
- _urllib_
- _optparse_
