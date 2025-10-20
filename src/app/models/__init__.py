# 导入 Base，它是所有模型的基础
from core.base_model import Base

# 导入你所有的模型，确保它们被 Base.metadata 识别
from .user import User

# 如果未来有其他模型，比如 Post, Item，也在这里导入
# from .post import Post
# from .item import Item

# 可选：使用 __all__ 来明确声明这个包对外暴露的接口
# 这是一种良好的编程习惯
__all__ = ["Base", "User"]
