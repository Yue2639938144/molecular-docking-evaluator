"""
分子对接结果优化排序工具安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取版本号
with open(os.path.join('src', '__init__.py'), 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip("'").strip('"')
            break
    else:
        version = '0.1.0'

# 读取README文件
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取依赖包
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='docking-evaluator',
    version=version,
    description='分子对接结果优化排序工具',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='开发团队',
    author_email='example@example.com',
    url='https://github.com/example/docking-evaluator',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'docking-evaluator=src.main:main',
        ],
    },
) 