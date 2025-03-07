from setuptools import setup, find_packages

setup(
    name="chan-agent",  # 包的名称
    version="0.0.10",    # 版本号
    author="Chan",
    author_email="925355568@qq.com",
    description="A simple llm agent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Chan-0312/chan-agent",  # 项目主页
    packages=find_packages(),  # 自动发现包
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",  # Python 的最低版本要求
    install_requires=[        # 运行时依赖的包
        "openai",
        "instructor",
        "google-generativeai",
        "filelock",
        "peewee"
    ],
)
