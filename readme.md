# init
```
git clone https://github.com/fi6uh/cloupy.git
cd cloupy
mkdir uploads
```

# running
```
cd cloupy/app
export FLASK_APP=clou.py
flask run
```

# using
In these examples, it is assumed this is running locally; change the socket to match your configuration.
```
# create a python script
echo 'print("Hello, world")' > hello.py

# cURL it up to ClouPy
curl -F"file=@hello.py" http://localhost:5000
# STDOUT: http://localhost:5000/run/ABC123.py

# cURL the execution endpoint to create a process execution job
curl http://localhost:5000/run/ABC123.py
# STDOUT: http://localhost:5000/view/ABC123.results

# cURL the results endpoint to send back the results of the process execution job (STDOUT)
curl http://localhost:5000/view/ABC123.results
# STDOUT: Hello, world
```

# purging
```
cd cloupy
rm uploads/*
cd app
sqlite3 cloupy.db < cloupy_purge.sql
```

# db rescue
If your database gets corrupted or deleted for whatever reason
```
cd cloupy/app
rm cloupy.db
sqlite3 cloupy.db < cloupy_init.sql
```
