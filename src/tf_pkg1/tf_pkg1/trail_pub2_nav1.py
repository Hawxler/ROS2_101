# trail_pub1_marker1.py에서 Point 대신 SLAM의 Path 메시지를 사용하여 잔상을 남기는 노드로 수정한 trail_pub2_nav1.py
import rclpy
from rclpy.node import Node
import tf2_ros

from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

class TrailPathPub1(Node):
    def __init__(self):
        super().__init__('trail_path_pub_node1')
        self.get_logger().info("Trail Path Publisher 노드 시작")

        #1. 잔상을 남길 프레임 지정
        self.target_frame = 'child1_frame'
        self.source_frame = 'world'

        #2. TF를 조회하기 위한 버퍼와 listener 생성
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        #3. Path 퍼블리셔 생성
        self.path_pubber = self.create_publisher(Path, 'trail_path_topic1', 10)

        #4. Path 메시지 생성 
        self.path_msg = Path()
        self.path_msg.header.frame_id = self.source_frame

        # 최대 저장할 경로 점 개수: Path 메시지에서 점 목록은 self.path_msg.poses에 저장됨
        self.max_path_length = 50
        
        #5. 타이머 설정 (0.1초마다 콜백 함수 호출)
        self.timer1 = self.create_timer(0.1, self.timer_callback)

    def timer_callback(self):
        #6. 현 시각 TF 정보 조회(예: 'world'에서 'child1_frame'까지의 변환 정보)
        try:
            lookup = self.tf_buffer.lookup_transform(
                self.source_frame,    # 기준(부모) 프레임
                self.target_frame,    # 찾을(자식) 프레임
                rclpy.time.Time()    # 최신 TF 정보 조회
            )
        except Exception as e:
            self.get_logger().warn(f"TF 정보 조회 실패({self.source_frame} to {self.target_frame}): {e}")
            return
        
        #7. Path 메시지에 위치/회전 정보 추가
        pose1 = PoseStamped()
        pose1.header.frame_id = self.source_frame
        pose1.header.stamp = self.get_clock().now().to_msg()

        pose1.pose.position.x = lookup.transform.translation.x
        pose1.pose.position.y = lookup.transform.translation.y
        pose1.pose.position.z = lookup.transform.translation.z

        # 회전은 Trail Path에서는 필요 없지만, TF에서 가져온 회전 정보도 포함시켜봄
        pose1.pose.orientation = lookup.transform.rotation

        self.path_msg.poses.append(pose1)
        
        # Path 메시지의 poses 리스트가 최대 길이를 초과하면 가장 오래된 점 제거
        # Point는 리스트를 따로 만들어서 관리해야 함. Path는 메시지 안에 poses라는 리스트가 있어서 그걸 이용하면 됨.
        if len(self.path_msg.poses) > self.max_path_length:
            self.path_msg.poses.pop(0)

        # Path 메시지의 header 시간 갱신
        self.path_msg.header.stamp = pose1.header.stamp

        #8. Publish
        self.path_pubber.publish(self.path_msg)

def main(args=None):
    rclpy.init(args=args)

    node1 = TrailPathPub1()
    rclpy.spin(node1)

    node1.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()