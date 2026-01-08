"""
Kubernetes Sandbox Service for isolated agent execution.
"""
import frappe
from typing import Optional


class SandboxService:
    """
    Manage Kubernetes sandbox pods for agent execution.

    Each agent session gets its own isolated pod with:
    - Filesystem (PVC)
    - Python/Node runtime
    - Resource limits
    """

    def __init__(self):
        """Initialize sandbox service with K8s config."""
        self.settings = frappe.get_single("Deep Agent Settings")
        self.namespace = self.settings.k8s_namespace or "frappe-agents"
        self.image = self.settings.sandbox_image or "python:3.11-slim"

        # Initialize K8s client
        self._init_k8s_client()

    def _init_k8s_client(self):
        """Initialize Kubernetes client."""
        from kubernetes import client, config

        try:
            # Try in-cluster config first (for pods)
            config.load_incluster_config()
        except Exception:
            try:
                # Fall back to local kubeconfig
                config.load_kube_config()
            except Exception as e:
                frappe.log_error(
                    title="K8s config failed",
                    message=str(e)
                )
                raise

        self.v1 = client.CoreV1Api()

    def create_sandbox(self, session_id: str) -> dict:
        """
        Create isolated sandbox pod for agent session.

        Args:
            session_id: Agent Session name

        Returns:
            dict with pod_name and pvc_name
        """
        from kubernetes import client

        # Sanitize session ID for K8s naming
        safe_id = session_id.lower().replace("_", "-")[:8]
        pod_name = f"sandbox-{safe_id}"
        pvc_name = f"sandbox-pvc-{safe_id}"

        # Create PVC for filesystem
        pvc = client.V1PersistentVolumeClaim(
            metadata=client.V1ObjectMeta(
                name=pvc_name,
                namespace=self.namespace,
                labels={
                    "app": "frappe-deep-agents",
                    "session": session_id
                }
            ),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=["ReadWriteOnce"],
                resources=client.V1ResourceRequirements(
                    requests={"storage": "1Gi"}
                )
            )
        )

        try:
            self.v1.create_namespaced_persistent_volume_claim(
                namespace=self.namespace,
                body=pvc
            )
        except Exception as e:
            if "AlreadyExists" not in str(e):
                raise

        # Create pod
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                namespace=self.namespace,
                labels={
                    "app": "frappe-deep-agents",
                    "session": session_id
                }
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="sandbox",
                        image=self.image,
                        command=["sleep", "infinity"],
                        working_dir="/workspace",
                        volume_mounts=[
                            client.V1VolumeMount(
                                name="workspace",
                                mount_path="/workspace"
                            )
                        ],
                        resources=client.V1ResourceRequirements(
                            limits={
                                "cpu": "1",
                                "memory": "2Gi"
                            },
                            requests={
                                "cpu": "500m",
                                "memory": "512Mi"
                            }
                        )
                    )
                ],
                volumes=[
                    client.V1Volume(
                        name="workspace",
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name=pvc_name
                        )
                    )
                ],
                restart_policy="Never"
            )
        )

        try:
            self.v1.create_namespaced_pod(
                namespace=self.namespace,
                body=pod
            )
        except Exception as e:
            if "AlreadyExists" not in str(e):
                raise

        # Wait for pod to be ready
        self._wait_for_pod(pod_name)

        return {
            "pod_name": pod_name,
            "pvc_name": pvc_name,
            "namespace": self.namespace
        }

    def _wait_for_pod(self, pod_name: str, timeout: int = 60):
        """Wait for pod to be running."""
        import time

        start = time.time()
        while time.time() - start < timeout:
            try:
                pod = self.v1.read_namespaced_pod(
                    name=pod_name,
                    namespace=self.namespace
                )
                if pod.status.phase == "Running":
                    return
            except Exception:
                pass
            time.sleep(2)

        raise TimeoutError(f"Pod {pod_name} not ready after {timeout}s")

    def exec_command(
        self,
        pod_name: str,
        command: list,
        timeout: int = 30
    ) -> str:
        """
        Execute command in sandbox pod.

        Args:
            pod_name: Name of the pod
            command: Command as list of strings
            timeout: Execution timeout in seconds

        Returns:
            Command output as string
        """
        from kubernetes.stream import stream

        try:
            resp = stream(
                self.v1.connect_get_namespaced_pod_exec,
                pod_name,
                self.namespace,
                command=command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
                _request_timeout=timeout
            )
            return resp
        except Exception as e:
            return f"Error: {str(e)}"

    def read_file(self, pod_name: str, file_path: str) -> str:
        """
        Read file from sandbox.

        Args:
            pod_name: Name of the pod
            file_path: Path relative to /workspace

        Returns:
            File contents as string
        """
        full_path = f"/workspace/{file_path.lstrip('/')}"
        return self.exec_command(pod_name, ["cat", full_path])

    def write_file(
        self,
        pod_name: str,
        file_path: str,
        content: str
    ) -> str:
        """
        Write file to sandbox.

        Args:
            pod_name: Name of the pod
            file_path: Path relative to /workspace
            content: File content to write

        Returns:
            Status message
        """
        full_path = f"/workspace/{file_path.lstrip('/')}"

        # Ensure parent directory exists
        parent_dir = "/".join(full_path.split("/")[:-1])
        if parent_dir:
            self.exec_command(pod_name, ["mkdir", "-p", parent_dir])

        # Write using heredoc
        # Escape content for shell
        escaped = content.replace("'", "'\\''")
        cmd = f"cat > {full_path} << 'EOFMARKER'\n{content}\nEOFMARKER"

        result = self.exec_command(pod_name, ["bash", "-c", cmd])
        return f"Written {len(content)} bytes to {file_path}"

    def list_files(self, pod_name: str, path: str = "") -> list:
        """
        List files in sandbox directory.

        Args:
            pod_name: Name of the pod
            path: Directory path relative to /workspace

        Returns:
            List of file info dicts
        """
        full_path = f"/workspace/{path.lstrip('/')}" if path else "/workspace"

        # Get file listing with details
        output = self.exec_command(
            pod_name,
            ["ls", "-la", full_path]
        )

        files = []
        for line in output.strip().split("\n")[1:]:  # Skip "total" line
            parts = line.split()
            if len(parts) >= 9:
                name = " ".join(parts[8:])
                if name not in [".", ".."]:
                    files.append({
                        "name": name,
                        "is_directory": parts[0].startswith("d"),
                        "size": parts[4],
                        "path": f"{path}/{name}".lstrip("/")
                    })

        return files

    def cleanup_sandbox(self, session_id: str):
        """
        Delete sandbox pod and PVC.

        Args:
            session_id: Agent Session name
        """
        safe_id = session_id.lower().replace("_", "-")[:8]
        pod_name = f"sandbox-{safe_id}"
        pvc_name = f"sandbox-pvc-{safe_id}"

        # Delete pod
        try:
            self.v1.delete_namespaced_pod(
                name=pod_name,
                namespace=self.namespace
            )
        except Exception as e:
            if "NotFound" not in str(e):
                frappe.log_error(
                    title=f"Pod deletion failed: {pod_name}",
                    message=str(e)
                )

        # Delete PVC
        try:
            self.v1.delete_namespaced_persistent_volume_claim(
                name=pvc_name,
                namespace=self.namespace
            )
        except Exception as e:
            if "NotFound" not in str(e):
                frappe.log_error(
                    title=f"PVC deletion failed: {pvc_name}",
                    message=str(e)
                )

    def get_pod_status(self, session_id: str) -> dict:
        """
        Get status of sandbox pod.

        Args:
            session_id: Agent Session name

        Returns:
            dict with pod status info
        """
        safe_id = session_id.lower().replace("_", "-")[:8]
        pod_name = f"sandbox-{safe_id}"

        try:
            pod = self.v1.read_namespaced_pod(
                name=pod_name,
                namespace=self.namespace
            )
            return {
                "name": pod_name,
                "phase": pod.status.phase,
                "ready": pod.status.phase == "Running"
            }
        except Exception as e:
            return {
                "name": pod_name,
                "phase": "Unknown",
                "ready": False,
                "error": str(e)
            }


def get_sandbox_service() -> Optional[SandboxService]:
    """
    Factory function to get sandbox service.

    Returns:
        SandboxService instance or None if K8s not configured
    """
    try:
        settings = frappe.get_single("Deep Agent Settings")
        if settings.enable_code_execution:
            return SandboxService()
    except Exception as e:
        frappe.log_error(
            title="Sandbox service init failed",
            message=str(e)
        )
    return None
