<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![project_license][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/cooperbocko/clashml">
    <img src="https://static.wikia.nocookie.net/clashroyale/images/5/54/KnightCard.png/revision/latest/thumbnail/width/360/height/450?cb=20250906092515" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Merge Tactics Machine Learning</h3>

  <p align="center">
    Creating a Reinforement Learning bot to play the Merge Tactics game mode in Clash Royale
    <br />
    <a href="https://github.com/cooperbocko/clashml"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/cooperbocko/clashml">View Demo</a>
    &middot;
    <a href="https://github.com/cooperbocko/clashml/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/cooperbocko/clashml/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This project aims to create a bot that can climb to a high rank in the Clash Royale game mode Merge Tactics. It is currently utilizing a simple DQN, but I have future plans to integrate other RL models as well.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Roboflow][Roboflow]][Roboflow-url]
* [![Python][Python]][Python-url]
* [![Pytorch][Pytorch]][Pytorch-url]
* [Ultralytics]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

* [Python 3.11](https://www.python.org/downloads/release/python-31311/)
* [Roboflow Account](https://roboflow.com)
* [Bluestackts]() (Optional; can use other emulators)
* Pytorch
  ```sh
  pip install torch
  ```
* Ultralytics
  ```sh
    pip install ultralytics
    ```
* PyAutoGUI
  ```sh
    pip install PyAutoGui
    ```
* Numpy
  ```sh
    pip install numpy
    ```
* CV2
* PIL
* Easyocr
* inference sdk
* dotenv
* clip
* sklearn

### Installation

1. Get a free API Key at [Roboflow](Roboflow-url)
2. Clone the repo
   ```sh
   git clone https://github.com/cooperbocko/clashml.git
   ```
3. Install packages
   ```sh
   pip install requirements.txt
   ```
4. Enter your API in `example.env`. Rename it and add it to your `.gitignore`
   ```
   ROBOFLOW_API_KEY = 'ENTER YOUR API';
   ```
5. Create your config file

    1. Open `example_config.json`
    2. Use the setup script `setup_helper.py` to show cursor coordinates for the points and regions you will be marking. 
    3. Get Left(x1), Top(y1), Right(x2), and Bottom(y2) coordinates of your emulator screen. It does not have to be perfect but make sure to not cut off any of the screen.
    ```sh
    "screen_bounds": {
        "left": x1,
        "top": y1,
        "right": x2,
        "bottom": y2
    },
    ```
      <img src="./images/readme/screen_bounds.png" alt="Screen Bounds Image" width="200" height="400">

      (For the rest of the setup images, a circle will denote just a point (x, y) while a square border will denote a region (x1, y1, x2, y2))

    4. For the following steps, use the `on_press()` function to take screenshots of the screens, then use an image editor to see the exact coordiantes of the screenshot you need. I like to use the cropping feature which will then show you the new image size, like 640x640, which also servers as your x and y coordiantes.
    Also, you should take screenshots of all the revelvant screens first and then go back fill out your config file.
    
    5. Naviagte to the main menu screen and take a screenshot. Then get the points for the variables below.
    ```sh
    "battle": [x, y],
    ...
    "menu_safe_click": [538, 684]
    ```
      <img src="./images/readme/battle_point.png" alt="Battle Point Image" width="200" height="400">

    6. Navigate to the main battle screen, take a screenshot, and get the points and regions for the variables below. 
    ```sh
    "card_regions": [
            [x1, y1, x2, y2],
            [x1, y1, x2, y2],
            [x1, y1, x2, y2]
        ],
        "elixr_region": [[x1, y1, x2, y2]],
        "placement_region": [[x1, y1, x2, y2]],
        ...,
        "phase_region": [[x1, y1, x2, y2]]
    ...
    "board": [
            [[x1, y1], [x1, y1], [x1, y1], [x1, y1], [x1, y1]],
            [[x1, y1], [x1, y1], [x1, y1], [x1, y1], [x1, y1]],
            [[x1, y1], [x1, y1], [x1, y1], [x1, y1], [x1, y1]],
            [[x1, y1], [x1, y1], [x1, y1], [x1, y1], [x1, y1]],
            [[x1, y1], [x1, y1], [x1, y1], [x1, y1], [x1, y1]]
        ],
        "hand": [
            [x1, y1],
            [x1, y1],
            [x1, y1]
        ],
        ...
        "safe_click": [x1, y1],
        "end_bar": [x1, y1],
    ```
      <img src="./images/readme/battle_screen.png" alt="Battle Point Image" width="200" height="400">

    7. In the main battle screen click a troop to navigate to the card image and level screen and take a screenshot. Next get the coordinates and regions for the variables below. 
    ```sh
    "card_picture_region": [[x1, y1, x2, y2]],
    "card_level_region": [[x1, y1, x2, y2]],
    ```
      <img src="./images/readme/card_image.png" alt="Battle Point Image" width="200" height="400">

    8. At the end of the game, navigate to the end screen, take a screenshot, and get the coordianates and regions for the variables below.
    ```sh
    "defeated_region": [[x1, y1, x2, y2]],
    "play_again_region": [[x1, y1, x2, y2]],
    "ok_region": [[x1, y1, x2, y2]],
    ...
    "play_again": [x1, y1],
    "ok": [x1, y1]
    ```
      <img src="./images/readme/defeated_screen.png" alt="Battle Point Image" width="200" height="400">

    9. Update the system settings in your config file. `is_mac_laptop_screen` is true if you are on a mac laptop and the emulator is on the laptop screen. `is_roboflow` is true if you are using roboflow instead of running detection models locally. Using roboflow is recommended for now as the local detection is not as accurate. `env_path` is just the path to your .env file you renamed in step 4.
      ```sh
      "system_settings": {
            "is_mac_laptop_screen": true,
            "is_roboflow": true,
            "env_path": "./example.env"
        },
      ```

6. In `setup_helper.py`, fill out the `phase_region` the same as you have in the config file, update the `path` and `filename` to the path and filename of the screenshot of the battle screen, and run the `make_phase_picture()` function. This will make one of two phase icons needed. During a game you have to have the max amount of troops place, like 2/2, for the other phase icon to appear. Once you do that, use the `on_press()` function to take another screenshot of it. Then, update the `path` and `filename` to the path and filename of this new screenshot, and run the `make_phase_picture()` function. Once you have both images, move them to the `images/phase` folder. Reference images are below.

<img src="./images/readme/solid.png" alt="Battle Point Image" width="100" height="100">
<img src="./images/readme/translucent.png" alt="Battle Point Image" width="100" height="100">

7. Finally, go to `train.py`, add the path to your config file to the `Agent()` constructor, and edit `bot.train()` to play how many games you want.
  ```
  bot = Agent('path/to/config.json', True)

  bot.train(# of games)
  ```

8. Run it!
  ```bash
  python train.py
  ```


<!-- USAGE EXAMPLES -->
## Usage

Loading...

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [1] Interactive Setup Helper
- [2] Distributed Training


See the [open issues](https://github.com/cooperbocko/clashml/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/cooperbocko/clashml/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=cooperbocko/clashml" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Cooper Bocko - [website](http://cooperbocko.github.io/)

Project Link: [https://github.com/cooperbocko/clashml](https://github.com/cooperbocko/clashml)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Best README Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/cooperbocko/clashml.svg?style=for-the-badge
[contributors-url]: https://github.com/cooperbocko/clashml/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/cooperbocko/clashml.svg?style=for-the-badge
[forks-url]: https://github.com/cooperbocko/clashml/network/members
[stars-shield]: https://img.shields.io/github/stars/cooperbocko/clashml.svg?style=for-the-badge
[stars-url]: https://github.com/cooperbocko/clashml/stargazers
[issues-shield]: https://img.shields.io/github/issues/cooperbocko/clashml.svg?style=for-the-badge
[issues-url]: https://github.com/cooperbocko/clashml/issues
[license-shield]: https://img.shields.io/github/license/cooperbocko/clashml.svg?style=for-the-badge
[license-url]: https://github.com/cooperbocko/clashml/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/cooperbocko
[product-screenshot]: images/screenshot.png
<!-- Shields.io badges. You can a comprehensive list with many more badges at: https://github.com/inttter/md-badges -->


[Roboflow]: https://img.shields.io/badge/Roboflow-6706CE?logo=Roboflow&logoColor=fff
[Roboflow-url]: https://roboflow.com
[Python]: https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff
[Python-url]: https://www.python.org
[Pytorch]: https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white
[Pytorch-url]: https://pytorch.org
[Ultralytics]: https://docs.ultralytics.com

[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
