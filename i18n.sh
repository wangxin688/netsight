pybabel extract -F babel.cfg -o message.pot .
pybabel init -i message.pot -d src/lang -l zh_CN
pybabel init -i message.pot -d src/lang -l en_US
pybabel compile -d /src/lang
rm message.pot