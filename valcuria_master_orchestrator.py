#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
valcuria_master_orchestrator.py - Valcuria Master System Orchestrator

Unified system orchestration for Valcuria ecosystem
Manages C bridge compilation, process lifecycle, and Python integration

License: MIT
Author: Valcuria / Tetsushi Sakagami
Version: 1.0.0
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [Valcuria-Master] %(message)s'
)


class ValcuriaMaster:
    """
    Master orchestrator for Valcuria system
    """

    def __init__(self):
        self.c_process = None
        self.python_bridge = None
        self.working_dir = Path.cwd()

    def compile_c_bridge(self) -> bool:
        """
        Compile C language bridge

        Returns:
            True if successful, False otherwise
        """
        logging.info("Compiling C bridge...")

        if sys.platform == "win32":
            cmd = ["cl", "valcuria_bridge_core.c", "ws2_32.lib", "/Fe:valcuria_bridge.exe"]
            output_file = "valcuria_bridge.exe"
        else:
            cmd = ["gcc", "valcuria_bridge_core.c", "-o", "valcuria_bridge"]
            output_file = "valcuria_bridge"

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logging.info(f"C bridge compiled successfully: {output_file}")
                return True
            else:
                logging.error(f"Compilation failed: {result.stderr}")
                return False
        except FileNotFoundError:
            logging.error(f"Compiler not found. Install gcc/clang or MSVC.")
            return False
        except Exception as e:
            logging.error(f"Compile error: {e}")
            return False

    def start_c_bridge(self) -> bool:
        """
        Start C bridge process

        Returns:
            True if successful, False otherwise
        """
        logging.info("Starting C bridge process...")

        bridge_exe = "valcuria_bridge.exe" if sys.platform == "win32" else "./valcuria_bridge"

        if not Path(bridge_exe).exists():
            logging.error(f"Bridge executable not found: {bridge_exe}")
            return False

        try:
            self.c_process = subprocess.Popen(
                [bridge_exe],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(1)  # Wait for port binding
            logging.info("C bridge process started")
            return True
        except Exception as e:
            logging.error(f"Failed to start C bridge: {e}")
            return False

    def run_python_tests(self) -> bool:
        """
        Run Python bridge tests

        Returns:
            True if successful
        """
        logging.info("Starting Python bridge tests...")

        try:
            from valcuria_bridge_python import ValcuriaBridge

            bridge = ValcuriaBridge()
            bridge.start()

            # Send test messages
            for i in range(3):
                logging.info(f"Test iteration {i+1}/3")
                bridge.test_send({"iteration": i + 1})
                time.sleep(1)

            time.sleep(2)

            # Print results
            responses = bridge.get_response_log()
            logging.info(f"Total responses received: {len(responses)}")
            for resp in responses:
                logging.info(f"Response: {resp['data']}")

            bridge.stop()
            logging.info("Python bridge tests complete")
            return True

        except Exception as e:
            logging.error(f"Python tests failed: {e}")
            return False

    def run_system(self) -> bool:
        """
        Run complete Valcuria system

        Returns:
            True if successful
        """
        logging.info("=" * 60)
        logging.info("Starting Valcuria Master System")
        logging.info("=" * 60)

        # Compile C bridge
        if not self.compile_c_bridge():
            logging.error("Failed to compile C bridge")
            return False

        # Start C bridge
        if not self.start_c_bridge():
            logging.error("Failed to start C bridge")
            return False

        # Run Python tests
        try:
            success = self.run_python_tests()
        except KeyboardInterrupt:
            logging.info("Interrupted by user")
            success = False

        # Cleanup
        self.shutdown()

        logging.info("=" * 60)
        logging.info("Valcuria Master System Complete")
        logging.info("=" * 60)

        return success

    def shutdown(self):
        """
        Shutdown all processes
        """
        logging.info("Shutting down...")

        if self.c_process:
            try:
                self.c_process.terminate()
                self.c_process.wait(timeout=5)
            except Exception as e:
                logging.warning(f"Error terminating C bridge: {e}")

        logging.info("System shutdown complete")


def main():
    """
    Main entry point
    """
    master = ValcuriaMaster()
    success = master.run_system()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
