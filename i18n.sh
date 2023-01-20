pybabel extract -F src/utils/babel.cfg -o src/messages.pot .
pybabel init -i src/messages.pot -d src/lang -l zh_CN
pybabel init -i src/messages.pot -d src/lang -l en_US
pybabel update -i src/messages.pot -d src/lang/
pybabel compile -d src/lang/
#rm message.pot

pybabel extract -F test_babel/utils/babel.cfg -o test_babel/messages.pot ./test_babel/
pybabel init -i test_babel/messages.pot -d test_babel/lang -l zh_CN
pybabel init -i test_babel/messages.pot -d test_babel/lang -l en_US
pybabel compile -d test_babel/lang/
