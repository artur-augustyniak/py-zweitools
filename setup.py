from setuptools import setup

setup(
    name='zweitools',
    version='0.1.0',
    license='BSD 2-clause',
    packages=['zweitools'],
    install_requires=[
        'pika==1.2.0',
        'jsonschema==2.6.0',
        'bravado-core==4.0.0',
        "IPy==1.1",
        "py-telegram-notifier==0.1.0.post2",
        "schwifty==2022.7.1",
        "validators==0.20.0",
        "ioc-fanger==4.0.0",
    ],

    classifiers=[
        'Development Status :: 1 - Yolo',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
