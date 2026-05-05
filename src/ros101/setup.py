from setuptools import find_packages, setup

package_name = 'ros101'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hawx',
    maintainer_email='icatching@daum.net',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'subber0_1 = ros101.subber0_1:main',
            'pubber0 = ros101.pubber0:main',
            'subber0 = ros101.subber0:main',
            'pubber1 = ros101.pubber1:main',
            'subber1 = ros101.subber1:main',
            'sub_msg1 = ros101.sub_msg1:main',
            'sub_msg2 = ros101.sub_msg2:main',
            'sub_msg3 = ros101.sub_msg3:main',
        ],
    },
)
