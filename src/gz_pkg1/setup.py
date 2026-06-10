from setuptools import find_packages, setup

package_name = 'gz_pkg1'

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
            'r1_cmd_pub1 = gz_pkg1.r1_cmd_pub1:main',
            'r1_odom_sub1 = gz_pkg1.r1_odom_sub1:main',
            'r1_dist1 = gz_pkg1.r1_dist1:main',
            'r1_rotate1 = gz_pkg1.r1_rotate1:main',
            'r1_square1 = gz_pkg1.r1_square1:main',
            'r1_cv_sub1 = gz_pkg1.r1_cv_sub1:main',
            'r1_cv_edge1 = gz_pkg1.r1_cv_edge1:main',
            'r1_imu_sub1 = gz_pkg1.r1_imu_sub1:main',
            'r1_imu_remo1 = gz_pkg1.r1_imu_remo1:main',
        ],
    },
)
