from setuptools import find_packages, setup

package_name = 'tf_pkg1'

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
            'static_tf_pub1 = tf_pkg1.static_tf_pub1:main',
            'tf_b1 = tf_pkg1.tf_b1:main',
            'tf_b2 = tf_pkg1.tf_b2:main',
            'tf_b2_1 = tf_pkg1.tf_b2_1:main',
            'tf_b2_2 = tf_pkg1.tf_b2_2:main',
            'tf_listen1 = tf_pkg1.tf_listen1:main',
            'trail_pub1_marker1 = tf_pkg1.trail_pub1_marker1:main',
            'trail_pub2_nav1 = tf_pkg1.trail_pub2_nav1:main',
            'trail_pub2_nav2 = tf_pkg1.trail_pub2_nav2:main',
        ],
    },
)
