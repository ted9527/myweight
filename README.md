# MyWeight

A weight record tool

V0.1 functionality:
1. add today's weight
2. delete any day's weight record
3. view the weight record the most 7 days or all days 
4. view the chart of weight record of the most 7 days or all days

V0.1 technology: 
1. Framework -- Flask
2. Form validation -- Flask-WTF
3. CSS -- Bulma
4. Front end (submit local date to server side) -- moment.js and jQuery3.5.1.js

## Installation

clone:
```
$ git clone https://github.com/ted9527/myweight.git
$ cd myweight
```
create & active virtual enviroment then install dependencies:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `. env/Scripts/activate` on Windows
$ pip install -r requirements.txt
```

generate fake data then run:
```
$ flask initdb
$ flask run
* Running on http://127.0.0.1:5000/
```

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).