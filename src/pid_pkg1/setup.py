from setuptools import find_packages, setup

package_name = 'pid_pkg1'

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
            'basics1_p1 = pid_pkg1.basics1_p1:main',
            'basics1_pi1 = pid_pkg1.basics1_pi1:main',
            'basics1_pid1 = pid_pkg1.basics1_pid1:main',
            'pid_para1 = pid_pkg1.pid_para1:main',
        ],
    },
)
