% Author: Jacob Hoffer
% Purpose: Support file for Phase Vision simulations
%          Convert google script generated test files to a saved .mat file
%          Convert parameters (variables) to a regular reference frame
% Date (Start): 01/19/2021
% Date (Last Edited): 01/19/2021

%% Clear Workspace, Command Window, Close any Windows
clear; clc, close all;

%% User Dependent Variables
% varaibles that may need to be changed by user for this program to run
FILE_NAME = "TestSet.m";

header = ["id", "omit", "A_gnd", "B_gnd", "C_gnd", "A_B", "B_C", "A_C",...
    "horizontal_offset", "line_frequency", "A_magnitude",...
    "B_magnitude", "C_magnitude", "A_angle", "B_angle", "C_angle",...
    "omit", "fs"];

%% Interate Through Test File
run(FILE_NAME);
clc;
for i = 1:size(matrix, 1)
    for ii = 1:length(matrix(i,:))
        eval(header(ii) + '=' + num2str(matrix(i,ii)) + ';');
    end
    
    ft_to_meter = 0.3048;
    
    % Convert so Origin @ Phase Vision
    phase_magnitude = [A_magnitude, B_magnitude, C_magnitude];
    phase_angles = [A_angle, B_angle, C_angle];
    phase_horizontal = ft_to_meter * (horizontal_offset - [0, A_B, A_C]);
    phase_vertical = ft_to_meter * [A_gnd, B_gnd, C_gnd];
    
    save(['test_files\test_', num2str(i), '.mat'], 'id', 'line_frequency', 'fs', 'phase_magnitude', 'phase_angles', 'phase_horizontal', 'phase_vertical');
    
end


 