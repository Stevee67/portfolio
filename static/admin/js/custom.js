/**
 * Created by Steve on 03.06.2016.
 */
var portfolioApp = angular.module('portfolio_app', [])
    .config(function ($interpolateProvider) {$interpolateProvider.startSymbol('{[{').endSymbol('}]}')});

portfolioApp.run(function($http) {
});


function flash(message) {
    $(".flash").remove();
    $('body').prepend(
        '<div class="flash">' +
            message +
        '</div>'
    );
    $(".flash").delay(4000).fadeOut();
}