coverage: 93%

#TC

TC is a simple message board writen in Flask, which is using for training intern.

In this project, we use three import module 'flask', 'wtform', 'blueprint'

##Run TC in debug mode

0. start the redis server

    ```
    service redis start
    ```

1. Modify 'config/common.cfg'

    ```
    debug = True
    port = 8080
    ```

2. Simply run

    ```
    python web.py
    ```

##Run TC as a formal product

                         redis 
       443                ||
user <====> nginx <====> uwsgi <====> flask
        8080 ||    9000 
inside <=====//

0. start the redis server

    ```
    service redis start
    (the database is stored in /var/lib/redis/dump.rdb) 
    ```

1. Modify 'config/common.cfg'

    ```
    debug = False
    port = 9000
    ```

2. Run on init.d

    ```
    service TC start
    service nginx start
    ```

3. if you want to start on boot

    ```
    chkconfig --level 2345 TC on 
    chkconfig --level 2345 nginx on 
    ```

##For test

1. run by test-script (warning, please backup your database before do this)

    ```
    cd tests
    sh pytest.sh
    ```
