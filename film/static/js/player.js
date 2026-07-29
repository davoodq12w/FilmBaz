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
            enableModifiersForNumbers: false
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

                player.currentTime(
                    Math.max(0, player.currentTime() - 10)
                );

                showSeekAnimation("backward", 10);

            }

            // 30 درصد سمت راست
            else if (clickX >= width * 0.7) {

                player.currentTime(
                    Math.min(player.duration(), player.currentTime() + 10)
                );

                showSeekAnimation("forward", 10);

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