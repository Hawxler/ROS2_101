import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtlePubber1(Node):
    def __init__(self):
        super().__init__('pubber_node1')

        self.pubber = self.create_publisher(
            Twist,
            'turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(1, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 2.0
        msg.angular.z = 1.0

        self.pubber.publish(msg)
        self.get_logger().info(
            f'Pub: linear={msg.linear.x}, angular={msg.angular.z}'
        )
    
def main(args=None):
    rclpy.init(args=args)

    node1 = TurtlePubber1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()