'use strict';
angular.module('myApp', ['ngRoute'])
  .controller('mainController', function($scope, $http) {
    $scope.documents = [];
    $scope.success = false;
    $scope.error = false;

    $scope.updateAvailability = function(data) {
        console.log("updateAvailability (" + data.date_slot + ") id = " + data.id + " booked = " + data.booked);
        var data = {
                id: data.id,
                booked: data.booked
            }
        $http.post('http://localhost:8080/bookings/availability/'+ data.id, data)
            .then(
                function(data, status) {
                    console.log("SUCCESS");
                    $scope.responsePOST = data;
                    console.log(data)
//                    console.log("RESPONSE updateAvailability (" + data.date_slot + ") id = " + data.id + " booked = " + data.booked);
                }
            )
    }


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


