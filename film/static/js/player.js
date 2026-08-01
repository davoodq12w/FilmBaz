$(function () {

    const player = videojs("movie-player", {
        userActions: {
            doubleClick: false
        }
    });

    player.ready(function () {

        player.hotkeys({
            volumeStep: 0.1,
            seekStep: 10,
            enableModifiersForNumbers: false,

            rewindKey: function () {
                return false;
            },

            forwardKey: function () {
                return false;
            }
        });

        const PLAY_REQUEST_INTERVAL = 60;
        const PAUSE_REQUEST_COOLDOWN = 20;

        let playTimer = null;

        let playTimerSeconds = 0;
        let pauseElapsedSeconds = PAUSE_REQUEST_COOLDOWN;

        let isSendingRequest = false;

        player.on("keydown", function (e) {

            if (e.which === 37) {
                e.preventDefault();
                seek(-10);
            }

            if (e.which === 39) {
                e.preventDefault();
                seek(10);
            }

        });

        const playerElement = player.el();

        playerElement.appendChild(
            document.getElementById("seek-backward-indicator")
        );

        playerElement.appendChild(
            document.getElementById("seek-forward-indicator")
        );

        const backwardIndicator = $("#seek-backward-indicator");
        const forwardIndicator = $("#seek-forward-indicator");

        let seekAnimationTimeout;

        function showSeekAnimation(direction) {

            clearTimeout(seekAnimationTimeout);

            const indicator =
                direction === "forward"
                    ? forwardIndicator
                    : backwardIndicator;

            $(".seek-indicator").removeClass("show");

            indicator.addClass("show");

            seekAnimationTimeout = setTimeout(() => {
                indicator.removeClass("show");
            }, 500);

        }

        function seek(seconds) {

            let targetTime = player.currentTime() + seconds;

            targetTime = Math.max(
                0,
                Math.min(player.duration(), targetTime)
            );

            player.currentTime(targetTime);

            showSeekAnimation(
                seconds > 0 ? "forward" : "backward"
            );

        }

        function startPlayTimer() {

            if (playTimer !== null) {
                return;
            }

            playTimer = setInterval(function () {

                playTimerSeconds++;
                pauseElapsedSeconds++;

                if (playTimerSeconds >= PLAY_REQUEST_INTERVAL) {
                    sendWatchRequest("play");
                }

            }, 1000);

        }

        player.on("play", function () {

            startPlayTimer();

        });


        player.on("pause", function () {

            clearInterval(playTimer);
            playTimer = null;

            if (pauseElapsedSeconds >= PAUSE_REQUEST_COOLDOWN) {
                sendWatchRequest("pause");
            }

        });

        player.on("ended", function () {

            clearInterval(playTimer);
            playTimer = null;

            sendWatchRequest("ended", true);

        });

        function sendWatchRequest(reason, completed = false) {

            if (isSendingRequest) {
                return;
            }

            isSendingRequest = true;
            clearInterval(playTimer);
            playTimer = null;
            $.ajax({

                url: "",
                type: "POST",

                data: {
                    current_time: Math.floor(player.currentTime()),
                    completed: completed
                },

                success: function (data) {

                    if (data) {

                        switch (reason) {

                            case "play":

                                playTimerSeconds = 0;
                                pauseElapsedSeconds = 0;

                                if (!player.paused()) {
                                    startPlayTimer();
                                }

                                break;

                            case "pause":

                                pauseElapsedSeconds = 0;

                                break;

                        }

                    } else {
                        console.log("error in saving watch progress.")
                    }
                },

                complete: function () {

                    isSendingRequest = false;

                }

            });

        }

        playerElement.addEventListener("dblclick", function (e) {

            // اگر روی کنترل‌های پلیر دابل کلیک شد، کاری انجام نده
            if (e.target.closest(".vjs-control-bar")) {
                return;
            }

            const rect = playerElement.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const width = rect.width;

            // 30 درصد سمت چپ
            if (clickX <= width * 0.3) {
                seek(-10);
            }

            // 30 درصد سمت راست
            else if (clickX >= width * 0.7) {

                seek(10);

            }

            // 40 درصد وسط
            else {

                if (player.isFullscreen()) {
                    player.exitFullscreen();
                } else {
                    player.requestFullscreen();
                }

            }

        });

        player.overlay({
            overlays: [
                {
                    start: 5,
                    end: 10,
                    content: '<div>Skip Intro</div>',
                    align: 'top'
                }
            ]
        });

        player.markers({
            markers: [
                {
                    time: 20,
                    text: 'Intro'
                },
                {
                    time: 80,
                    text: 'Fight'
                }
            ]
        });

    });

});