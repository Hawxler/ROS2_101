from setuptools import find_packages, setup
# Launch 데이터 파일 경로 조합용
import os
from glob import glob

package_name = 'launcher_pkg1'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # share/launcher_pkg1/launch라는 폴더를 만들어라.
        # launch 폴더 안에 있는 *.launch.py 파일 찾아라.
        # 즉, 찾은 .launch.py 파일 모두를 share/.../launch 폴더에 복사해라.
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.xml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hawx',
    maintainer_email='oppaha9@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pubber1=launcher_pkg1.pubber1:main',
        ],
    },
)
