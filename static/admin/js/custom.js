/**
 * Created by Steve on 03.06.2016.
 */
var portfolioApp = angular.module('portfolio_app', [])
    .config(function ($interpolateProvider) {$interpolateProvider.startSymbol('{[{').endSymbol('}]}')});

portfolioApp.run(function($http) {
});


portfolioApp.directive('pfDate', function () {
        return {
            replace: false,
            restrict: 'A',
            scope: {
                pfDate: '='
            },
            link: function (scope, element, attrs, model) {
                if(scope['pfDate'] === null){
                    element.text('Present')
                }else{
                    element.text(scope['pfDate'])
                }
                scope.$watch('pfDate', function (nv, ov) {
                    scope.setdate = scope['pfDate'];
                });
                scope.$watch('setdate', function (nv, ov) {
                    if (nv && nv.setHours) nv.setHours(12);
                    scope['ngModel'] = nv;
                });
            }
        }
});


function callBackAfterReadFile(file, func, data) {
    if(file){
        var fr = new FileReader();
        fr.onload = function (e) {
            data['file'] = {'mime': file.type, 'name': file.name, 'content': fr.result}
            func(data)
        };
        fr.onerror = function (e) {
            flash('File loading error');
        };
        fr.readAsDataURL(file);
    }else{
        func(data)
    }

  }

function flash(message) {
    $(".flash").remove();
    $('body').prepend(
        '<div class="flash">' +
            message +
        '</div>'
    );
    $(".flash").delay(4000).fadeOut();
}