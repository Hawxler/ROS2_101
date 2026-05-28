# trail_pub2_nav2.py에 텍스트 출력을 추가해서 거리를 보여줌.
import math
import rclpy
from rclpy.node import Node
import tf2_ros

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import Float64
from visualization_msgs.msg import Marker

class TrailPathPub2(Node):
    def __init__(self):
        super().__init__("trail_path_pub_node2")
        self.get_logger().info("Trail Path Pub 노드2 시작")
        
        #1. 잔상을 남길 프레임 지정
        self.target_frame = "child1_frame"
        self.source_frame = 'world'

        #2. TF를 조회하기 위한 버퍼와 listener 생성
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        #3. Path 퍼블리셔 생성
        self.path_pubber = self.create_publisher(Path, 'frame_path_topic1', 10)

        #4 Path 메시지 생성
        self.path_msg = Path()
        self.path_msg.header.frame_id = self.source_frame

        #5. 최대로 저장할 경로 점 개수: Path 메시지에서 점 목록은 self.path_msg.poses에 저장됨
        self.max_path_length = 50

        #6. 거리를 발행하기 위한 publisher
        self.dist_pubber = self.create_publisher(Float64, 'child_dist_topic1', 10)
        self.marker_pubber = self.create_publisher(Marker, 'dist_marker_topic1', 10)

        self.timer1 = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        #7. 현 시점 TF 정보 조회(예: 'world'에서 'child1_frame'까지의 변환 정보)
        try:
            lookup = self.tf_buffer.lookup_transform(
                self.source_frame,   #기준(부모) 프레임
                self.target_frame,   #찾을(자식) 프레임
                rclpy.time.Time()    #최신 TF 정보 조회
            )
        except Exception as e:
            self.get_logger().warn(f"TF 정보 조회 실패({self.source_frame} to {self.target_frame}): {e}")
            return
        
        #8. Path 메시지에 변환(위치/회전) 정보 추가
        pose1 = PoseStamped()
        pose1.header.frame_id = self.source_frame
        pose1.header.stamp = self.get_clock().now().to_msg()

        pose1.pose.position.x = lookup.transform.translation.x
        pose1.pose.position.y = lookup.transform.translation.y
        pose1.pose.position.z = lookup.transform.translation.z

        # 회전은 Trail Path에서는 필요 없지만, TF에서 가져온 회전 정보도 추가해봄.
        pose1.pose.orientation = lookup.transform.rotation

        self.path_msg.poses.append(pose1)

        if len(self.path_msg.poses) > self.max_path_length:
            self.path_msg.poses.pop(0)

        # Path 메시지의 header 시간 갱신
        self.path_msg.header.stamp = pose1.header.stamp

        #9. Path 발행
        self.path_pubber.publish(self.path_msg)

        #10. world 기준 child1_frame의 거리 계산(유클리드)
        dx = lookup.transform.translation.x
        dy = lookup.transform.translation.y
        dz = lookup.transform.translation.z
        distance1 = math.sqrt(dx**2 + dy**2 + dz**2)

        #11. 거리 발행: Float64 메시지
        dist_msg1 = Float64()
        dist_msg1.data = distance1
        self.dist_pubber.publish(dist_msg1)

        #12. 거리 텍스트 설정: Marker 메시지
        marker1 = Marker()
        marker1.header.frame_id = self.source_frame
        marker1.header.stamp = self.get_clock().now().to_msg()
        marker1.ns = "distance"
        marker1.id = 0
        marker1.type = Marker.TEXT_VIEW_FACING
        marker1.action = Marker.ADD

        #13. Marker를 child_frame 바로 위에 표시하도록 설정(z축으로 약간 오프셋)
        marker1.pose.position.x = dx
        marker1.pose.position.y = dy
        marker1.pose.position.z = dz + 0.5

        #14. 텍스트 크기, 색상 설정
        marker1.scale.z = 0.5   # 텍스트 높이
        marker1.color.a = 1.0   # 불투명
        marker1.color.r = 1.0
        marker1.color.g = 1.0
        marker1.color.b = 1.0

        #15. Marker 텍스트 발행
        marker1.text = f"Dist: {distance1:.2f}m"
        self.marker_pubber.publish(marker1)

def main(args=None):
    rclpy.init(args=args)

    node1 = TrailPathPub2()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()