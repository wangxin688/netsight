pybabel extract -F src/utils/babel.cfg -o src/messages.pot .
pybabel init -i src/messages.pot -d src/lang -l zh_CN
pybabel init -i src/messages.pot -d src/lang -l en_US
pybabel update -i src/messages.pot -d src/lang/
pybabel compile -d src/lang/
#rm message.pot