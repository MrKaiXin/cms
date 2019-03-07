import qiniu
access_key = "IB08aRqFamgxz6sfvlAZM6py4Hz-BB0VaPybdxye"
secret_key = "OjYSkHfYRsslhuPC2TXa6FRaVeNxurw5d1Lzs7Wu"
bucket_name = "dongliqihang"


def storage(data):
    '''
        access_key      秘钥管理 - AK
        secret_key      秘钥管理 - SK
        bucket_name     空间名

        data就是要上传的数据
        key是这个数据的键（就是七牛给这个图片起的名字，我们可以通过它拿到保存在七牛的这张图片）
    '''
    try:
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = qiniu.put_data(token, None, data)
        print(ret)
        print(info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")

    # 返回七牛中保存的图片名
    return ret["key"]


if __name__ == "__main__":
    with open('/home/python/Desktop/fruit.jpg', "rb") as f:
        img_data = f.read()

    storage(img_data)

    #
    # key值 FlwG0f-SsMEoNTDtoiLXFJ_wOfgq
    # http://pj9p8snfa.bkt.clouddn.com/FlwG0f-SsMEoNTDtoiLXFJ_wOfgq
    # http://pj9p8snfa.bkt.clouddn.com/ + key
    # http://pj9p8snfa.bkt.clouddn.com/ + storage(用户上传过来的图片)