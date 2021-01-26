% Author: Jacob Hoffer
% Purpose: Load .mat files and run simulation
%          Return rsm error
% Date (Start): 01/19/2021
% Date (Last Edited): 01/19/2021

clear; clc;

TEST_FILE_DIRECTORY = "Z:\adit\My Documents\GitHub\Phase_Vision\test_files";
test_files = dir(fullfile(TEST_FILE_DIRECTORY, '*.mat'));

for i = 1:length(test_files)
    load("Z:\adit\My Documents\GitHub\Phase_Vision\test_files\" + test_files(i).name);
end