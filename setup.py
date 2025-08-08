from setuptools import setup

setup(
    name='siglent-visa',
    version='0.2.0',    
    description='A library to manage Siglent instruments, via the VISA interface',
    readme = "README.md",
    url= 'https://github.com/GramazioFrancesco/siglent-visa',
    author='Gramazio Francesco, Thomas Blum (tfblum)',
    author_email='gramazio.francesco@lab3841.it',
    license='MIT',
    packages=['sdg1000', 'sdg2000x'],
    install_requires=['pyvisa'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",            
        "Operating System :: OS Independent",               
        "Topic :: Utilities",
    ],
)