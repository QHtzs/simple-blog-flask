# simple-blog-flask
基于python flask 的简单非交互blog

[详情](./b_app/readme.md)

## socket部分
* 由于只是demo，sql语句发送时，没有定义包尾，且默认最大传输是MAX_INT16 65536,实际当内容较多时是会超过这个长度的，可以自定义包，以便支持更大的数据传输。数据接收时可以分片拼接

