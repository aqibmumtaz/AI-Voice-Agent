from configs import Configs
import os
import shutil


class Utils:
    """
    Helper functions for the AI Voice Agent project.
    """

    @staticmethod
    def print_api_key():
        print(f"Retell API Key: {Configs.RETELL_API_KEY}")

    @staticmethod
    def clear_dir(directory_path):
        """
        Deletes all files and subdirectories in the specified directory.
        """

        if not os.path.isdir(directory_path):
            print(f"{directory_path} is not a valid directory.")
            return

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

    # Add more helper methods as needed
