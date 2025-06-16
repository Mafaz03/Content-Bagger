import instaloader
import os
import time
import shutil
from config import *
from helper import *
class Folder_Organiser():
    def __init__(self, folder):
        self.folder = folder
        self.mp4_exists = None
        self.jpg_exists = None
        self.num_mp4 = None

    # @staticmethod
    def _is_a_folder_of_post(self):
        txt_exists = False
        self.jpg_exists, self.num_jpg = False, 0
        self.mp4_exists, self.num_mp4 = False, 0

        for file in os.listdir(self.folder):
            if file.endswith(".mp4"): 
                self.mp4_exists = True
                self.num_mp4 += 1

            if file.endswith(".jpg"): 
                self.jpg_exists = True
                self.num_jpg += 1

            if file.endswith(".txt"): txt_exists = True
        
        if self.jpg_exists: self.nature = ""
        return (txt_exists and self.jpg_exists) or (txt_exists and self.mp4_exists)

    def organise(self):
        if self._is_a_folder_of_post():
            thumbnails_and_mp4 = {}
            files = os.listdir(self.folder)

            if self.mp4_exists: # Find thumbnail
                for file in files:
                    if file.endswith(".jpg"):     
                        thumbnail_path = file.removesuffix(".jpg") + ".mp4"
                        if thumbnail_path in files:         # if a jpg is corresponding to a mp4, then that jpg is its thumbnail
                            thumbnails_and_mp4[file] = thumbnail_path
                        else:                               # else its a standalone image
                            thumbnails_and_mp4[file] = file
            elif self.jpg_exists:
                for file in files:
                    if file.endswith(".jpg"): 
                        thumbnails_and_mp4[file] = file

        else: print("Not a folder that has saved posts")
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(self.folder, file), 'r') as f:
                    caption = f.read()
                break

        return sorted(thumbnails_and_mp4.items()), caption
    
class Fetcher():
    def __init__(self, 
                 target_accounts,   # List of accounts
                 get_per_accs = 1,  # How many posts to get from each account
                 delay_per_post = 0,
                 ):
        if isinstance(target_accounts, str): target_accounts = [target_accounts]
        assert type(target_accounts) == list, "Make sure `target_accounts` is a list"

        self.target_accounts = target_accounts
        self.get_per_accs = get_per_accs
        self.delay_per_post = delay_per_post

        assert self.get_per_accs <= 10, "Keep it below 10 bruv"

        self.ig = instaloader.Instaloader()
    
    def fetch_content(self):
        with open("posted.txt", "r") as f:
            posted = f.readlines()
            posted = [int(i) for i in posted if i != "\n"]

        for account in self.target_accounts:
            print(f"\n--- {account} ---")
            count = 0
            profile = instaloader.Profile.from_username(self.ig.context, account)
            for post in profile.get_posts():
                target_path = os.path.join(CONTENT_FOLDER, str(post.mediaid))

                # instaloader download is causing issue when saving a post it replaces / [U+002f] with ∕ [U+2215]
                # Causing post to be saved in home dir
                # Solving: 1. Saving in home  
                #          2. Moving to content dir
                
                if post.mediaid in posted:
                    print("Content already posted...Skipping...")
                    if not post.is_pinned:
                        count += 1
                else:   
                    self.ig.download_post(post, target = str(post.mediaid)) # 1.
                    shutil.move(str(post.mediaid), target_path)             # 2.

                    with open("posted.txt", "a") as f:
                        f.write(f"\n{str(post.mediaid)}")

                    time.sleep(self.delay_per_post)
                    count += 1

                if count >= self.get_per_accs: break
                
        delete_files_with_extensions(CONTENT_FOLDER)

    def clear_folder(self,):
        if os.path.exists(CONTENT_FOLDER):
            shutil.rmtree(CONTENT_FOLDER)
            print(f"Cleared folder: {CONTENT_FOLDER}")
        os.makedirs(CONTENT_FOLDER, exist_ok=True)
    