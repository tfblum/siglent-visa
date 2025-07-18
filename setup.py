from setuptools import setup

setup(
    name='siglent-visa',
    version='0.1.0',    
    description='A library to manage Siglent instruments, via the VISA interface',
    readme = "README.md",
    url='https://github.com/shuds13/pyexample',      ###
    author='Gramazio Francesco',
    author_email='gramazio.francesco@lab3841.it',
    license='MIT',
    packages=['sdg2000x'],
    install_requires=['pyvisa'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",            
        "Operating System :: OS Independent",               
        "Topic :: Utilities",
    ],
)