"""
sqlalchemy ORM cascade:
1. save-update,merge:default, 在添加一条数据时，会把其他和他相关联的数据
添加到数据库中
2. delete: 当删除某一个model中的数据是，是否也删除relationship相关联的数据(默认情况会覆盖

)
3. delete-orphan: 当一个orm对象解除了父表中关联对象时，自己便会被删除。父表数据删除时，
自己也会被删除。用于一对多，不能用于多对多以及多对一
"""
