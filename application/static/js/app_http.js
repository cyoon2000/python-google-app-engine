'use strict';
angular.module('myApp', ['ngRoute'])
  .controller('mainController', function($scope, $http) {
    $scope.documents = [];
    $scope.success = false
    $scope.error = false
    $http.get('http://localhost:8080/bookings/availability/unit/11')
        .then(
            function(result) {
                console.log("SUCCESS");
                $scope.documents = result.data;
                console.log('data length = ' + $scope.documents.data.length)
                $scope.error = true;
            },
            // OnFailure function
            function(reason) {
                console.log("ERROR")
                console.log(reason)
                $scope.somethingWrong = reason;
                $scope.error = true;
            }
        )
    });
