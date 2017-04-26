(function () {

  'use strict';

  angular.module('YTD', [])

  .controller('YTDController', ['$scope', '$log',
    function($scope, $log) {
    $scope.getResults = function() {
      $log.log("test");
    };
  }

  ]);

}());