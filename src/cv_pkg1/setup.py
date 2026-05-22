from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'cv_pkg1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.xml')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hawx',
    maintainer_email='oppaha9@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'img_sub1 = cv_pkg1.img_sub1:main',
            'img_pub1 = cv_pkg1.img_pub1:main',
            'img_pub2 = cv_pkg1.img_pub2:main',
            'img_pub3 = cv_pkg1.img_pub3:main',
            'img_pub4 = cv_pkg1.img_pub4:main',
            'img_pub5 = cv_pkg1.img_pub5:main',
            'img_pub6 = cv_pkg1.img_pub6:main',
            'img_pub7 = cv_pkg1.img_pub7:main',
        ],
    },
)
