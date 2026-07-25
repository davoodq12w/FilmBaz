$(function () {

    const player = videojs("movie-player");

    player.ready(function () {

        player.hotkeys({
            volumeStep: 0.1,
            seekStep: 10,
            enableModifiersForNumbers: false
        });

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