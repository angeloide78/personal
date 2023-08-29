from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='personal',
    version='1.0.0',
    author='Ángel Luis García García',
    author_email='angelluis78@gmail.com',
    description='Gestión de personas',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/angeloide78/personal',
    packages=find_packages(),
    include_package_data=True,  
    install_requires=[
        'reportlab',
        'sqlalchemy',
        'pillow==9.0.1',
        'pyqt6==6.5.2' 
        ],
    package_data={
           'personal': ['model/personal.db',
                        'assets/imagenes/*.png',
                        'assets/img_doc/*.png',
                        'view/*.ui']
       },    
    entry_points={
        'console_scripts': [
        'personal = personal.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
)


