/**
 * Created by Steve on 03.06.2016.
 */
var portfolioApp = angular.module('portfolio_app', [])
    .config(function ($interpolateProvider) {$interpolateProvider.startSymbol('{[{').endSymbol('}]}')});

portfolioApp.run(function($rootScope, $http) {
    angular.extend($rootScope, {
        update_list: function (list, new_element) {
            for(var i=0;list.length>i;i++){
                if(list[i]['id'] == new_element['id']){
                    list[i] = new_element
                }
            }
        },
        delete_element: function (list, new_element) {
            for(var i=0;list.length>i;i++){
                if(list[i]['id'] == new_element['id']){
                    delete list[i]
                }
            }
        }
    })

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
}).directive('pfRequired', function ($timeout) {
        return {
            replace: false,
            restrict: 'A',
            scope: {
                ngModel: '='
            },
            link: function (scope, element, attrs, model) {

                var Error = false;

                element.click(function(){
                    $timeout(function () {
                        errorMsg(element)
                    }, 700)
                });

                scope.$watch('ngModel', function (nv, ov) {
                    if(isEmpty(scope['ngModel'])){
                        element.addClass('invalid');
                    }else{
                        element.removeClass('invalid')
                    }
                });

                function errorMsg(element) {
                    if(!Error && isEmpty(element.context.value)){
                        element.after('<span id="error-msg">'+'Fill out required fields - `'+ attrs.ngModel.split('.')[1]+'`!'+'</span>');
                        Error = true;
                        $timeout(function () {
                            $('#error-msg').remove();
                            Error = false
                        }, 1500)
                    }
                }
            }
        }
}).directive('pfSave', function ($http, $timeout) {
        return {
            replace: false,
            restrict: 'A',
            scope: {
                pfSave: '=',
                pfRequiredFields: '='
            },
            link: function (scope, element, attrs, model) {
                
                var buttonDOMElement = document.querySelector('#'+attrs['id']);

                var button = angular.element(buttonDOMElement);

                var onButtonClick = function () {
                    var url = scope['pfSave'].hasOwnProperty('id')?window.location.pathname+'?edit': window.location.pathname+'?add';
                    var modal = $('#'+getModalId())
                    if(ifAllow() === true){
                       return $http({ method: 'PUT',url: url, data: scope['pfSave']}).then(function successCallback(response) {
                           if(modal){
                               $timeout(function () {
                                  modal.modal('hide')
                               }, 500)
                           }

                           if(scope.$parent.hasOwnProperty('list_data')){
                               if(scope['pfSave'].hasOwnProperty('id')){
                                    scope.$parent.update_list(scope.$parent.list_data, response.data.data)
                               }else {
                                    scope.$parent.list_data.push(response.data.data)
                               }
                           }else if(scope.$parent.hasOwnProperty('data')){
                               scope.$parent.data = response.data.data;
                               if('success' in response.data)
                                   flash(response.data.success)
                           }
                       }, function errorCallback() {
                           flash('Server error!')
                       });
                    }else{
                        flash('Fill out required fields!')
                    }
                };
            
                button.on('click', onButtonClick);
            
                scope.$on('$destroy', function () {
                    button.off('click', onButtonClick);
                });

                function getModalId() {
                    var id = attrs['id'].split('_')[1];
                    if(id)
                        return 'add'+id.capitalizeFirstLetter();
                }
                
                function ifAllow() {
                    return check_required_fields(scope.$parent.required_fields,scope['pfSave'])
                }
            }
        }
})


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

function check_required_fields(list_of_r_fields, pass_fields) {
    for(var i=0;list_of_r_fields.length>i;i++){
        if(pass_fields.hasOwnProperty(list_of_r_fields[i]) && isEmpty(pass_fields[list_of_r_fields[i]])){
            return 'Fill in '+ list_of_r_fields[i]
        }
    }
    return true
}

function chech_date_from_to(from, to) {
    if(!from){
       flash('Fill in `from` date!');
        return false 
    }
    if(from>=to){
        flash('First date must be smaller than first!');
        return false
    }
    return true
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

function isEmpty(element) {
    return element === '' || element === 0 || element === null
}

String.prototype.capitalizeFirstLetter = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}