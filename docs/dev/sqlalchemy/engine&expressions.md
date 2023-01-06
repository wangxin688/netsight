# sqlalchemy开发参考手册(Async version)
## why ORM?
### 优势
1. 自动处理了db和python object的之间的映射关系，屏蔽两套系统之间的差异，无需编写复杂的sql，直接操作object即可
2. 屏蔽了各个db之间的差异，除db特殊的类型支持和dialect，绝大部份场景更换db可以无需调整
3. 使db结构文档话，models定义清晰的描述了db的表结构和E-R，同时migrations文件引入非常便利的版本管理
4. 避免不规范，冗余，风格不统一的sql语法和人为bug，方便维护
### 劣势
1. ORM需要消耗额外的性能来处理对象关系和映射，通过orm做多表关联查询或复杂的sql查询时，效率较低，适用于场景不太复杂，性能要求不太苛刻的场景
2. ORM会带来额外的学习成本，native sql吃遍天下

sqla分为两部分， core/ORM，对比django的ORM, db连接和orm混在一起

core层主要实现客户端连接池，rdbms通常并发连接能力不强，在web应用中为了减少短连接，增加了连接池设计。
- 服务端连接池： 连接池中间件，给短连接每次分配一个长链接服用
- 客户端连接池： 三方代码库引用，如sql. sqla维护了一定数量的长链接，当调用connect时，实际是从连接池取出了一个连接，调用close时，实际是放回到了池子中的一个连接

## Engine
sqla使用`create_engine`来创建连接池
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.session import sessionmaker

from src.core.config import settings

async_sqlalchemy_database_uri = settings.SQLALCHEMY_DATABASE_URI

async_engine = create_async_engine(
    async_sqlalchemy_database_uri,
    pool_pre_ping=True,
    future=True, # 使用sqla 2.0 API，向后兼容
    echo=True,  # 打印实际执行的sql, 调试使用
    pool_size=settings.POOL_SIZES, # 默认连接池大小为5，0为不限制
    pool_recycle=settings.POOL_RECYCLE # 设置时间以限制db自动断开连接
)
```
### Session
1. API Depends session, session可以作为参数在函数间逐层传递
注意： session本身不是线程安全的，所以推荐从api接口向内层函数传递，libs和service不直接取用新的session
```python
async_session: AsyncSession = sessionmaker(
    async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)

# 已自动实现上下文管理， close session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield 

```
2. 非API接口业务，如定时任务场景
```python
async def get_async_session() -> AsyncGenerator:
    try:
        session: AsyncSession = async_session()
        logger.debug(f"ASYNC Pool: {async_engine.pool.status()}")
        yield session
    except SQLAlchemyError as sql_ex:
        await session.rollback()
        raise sql_ex
    finally:
        await session.close()
```

## object Mapping
参考项目文件

## Basic CRUD
参考CRUDBase，这样主要提供部分复杂查询以及pg特殊字段的dialect, 参考项目模块

## foreignKey和relationship
> site-hosts，对多对模型 teacher<->class
### foreignKey
1. 外键约束： 用于在删除或更新某个值或行是，对主键/外键关系中的一组数据列强制进行操作的限制
    `ondelete`和`onupdate`参数，可选值
    1. 默认行为 `NO ACTION`: 即什么都不做，直接报错
    2. `CASCADE`: 删除/更新浮标数据，从表数据会同时被删除/更新，无报错
    3. `RESTRICT`: 不允许直接删除/更新父表，直接报错。
    4. `SET NULL` or `SET DEFAULT`：删除/更新父表数据时，将对应从表数据充值为NULL或默认值
2. 唯一性约束：UniqueConstraint("vlan_group_id", "vlan_id"), 例如在一组vlan_group中，不能出现两个vlan 300的id
3. checkConstraint, 通常不建议使用，在上层业务处理
4. 主键约束

### relationship
relationship函数在ORM中用户构建表之间的关联关系，与ForeignKey不同的是，它定义的关系不属于表定义，而是动态计算的

### backref和back_populates
backref和back_populates作用相同，一个为隐式声明，一个为显示声明，项目中推荐使用显示声明，虽然多了一行代码，但是对象之间的关系更为清晰

### primaryjoin和secondaryjoin
- primaryjoin：（多对多中）用于从子对象查询其父对象的 condition（child.parents），默认只考虑外键。
- secondaryjoin：（多对多中）用于从父对象查询其所有子对象的 condition（parent.children），同样的，默认情况下只考虑外键。

### ORM `delete` cascade和foreignKey的`ondelete` cascade
上文中Table 定义中的级联操作：ON DELETE 和 ON UPDATE，可以通过 ForeignKey 的参数指定为 CASCADE.
sqla 还有一个 relationship 生成 SQL 语句时的配置参数 cascade，另外 passive_deletes 也可以指定为 cascade。
这三个 cascade 到底有何差别呢？
外键约束中的 ON DELETE 和 ON UPDATE，与 ORM 层的 CASCADE 在功能上，确实有很多重叠的地方。但是也有很多不同：

- 数据库层面的 ON DELETE 级联能高效地处理 many-to-one 的关联；我们在 many 方定义外键，也在这里添加 ON DELETE 约束。而在 ORM 层，就刚好相反。SQLAlchemy 在 one 方处理 many 方的删除操作，这意味着它更适合处理 one-to-many 的关联。
- 数据库层面上，不带 ON DELETE 的外键常用于防止父数据被删除，而导致子数据成为无法被索引到的垃圾数据。如果要在一个 one-to-many 映射上实现这个行为，sqla将外键设置为 NULL 的默认行为可以通过以下两种方式之一捕获：
- 最简单也最常用的方法，当然是将外键定义为 NOT NULL. 尝试将该列设为 NULL 会触发 NOT NULL constraint exception.
- 另一种更特殊的方法，是将 passive_deletes 标志设置为字 all. 这会完全禁用 SQLAlchemy 将外键列设置为 NULL 的行为，并且 DELETE 父数据而不会对子数据产生任何影响。这样才能触发数据库层面的 ON DELETE 约束，或者其他的触发器。数据库层面的 ON DELETE 级联 比 ORM 层面的级联更高效。数据库可以同时在多个 relationship 中链接一系列级联操作。sqla不需要这么复杂，因为我们通过将 passive_deletes 选项与正确配置的外键约束结合使用，提供与数据库的 ON DELETE 功能的平滑集成。
#### ORM 层的 cascade 实现
relationship 的 cascade 参数决定了修改父表时，什么时候子表要进行级联操作。它的可选项有（str，选项之间用逗号分隔）：

- `save-update`：默认选项之一。在 add（对应 SQL 的 insert 或 update）一个对象的时候，会 add 所有它相关联的对象。
- `merge`：默认选项之一。在 merge（相当字典的update操作，有就替换掉，没有就合并）一个对象的时候，会 merge 所有和它相关联的对象。
- `expunge` ：移除操作的时候，会将相关联的对象也进行移除。这个操作只是从session中移除，并不会真正的从数据库中删除。
- `delete`：删除父表数据时，同时删除与它关联的数据。
- `delete-orphan`：当子对象与父对象解除关系时，删除掉此子对象（孤儿）。（其实还是没懂。。）
- `refresh-expire`：不常用。
- `all`：表示选中除 delete-orphan 之外的所有选项。（因此 all, delete-orphan 很常用，它才是真正的 all）
默认属性是 `save-update, merge`.

详细文档见 SQLAlchemy - Cascades

#### 数据库层的 cascade 实现
- 将 ForeignKey 的 `ondelete`和`onupdate` 参数指定为`CASCADE`，实现数据库层面的级联。
- 为 `relationship` 添加关键字参数`passive_deletes="all"`，这样就完全禁用sqla将外键列设置为 NULL 的行为，并且 DELETE 父数据不会对子数据产生任何影响。这样 DELETE 操作时，就会触发数据库的`ON DELETE`约束，从而级联删除子数据。

