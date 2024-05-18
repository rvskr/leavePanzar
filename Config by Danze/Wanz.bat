xcopy ".\CVarGroups" "..\..\Game\Config\CVarGroups\" /y
xcopy ".\Config" "..\..\Game\Config\" /y
copy .\d3d9.dll ..\..\Bin64
copy .\dxvk.conf ..\..\Bin64
copy .\PnzCl.dxvk-cache ..\..
copy .\PnzCl_d3d9.log ..\..
copy .\dxvk.conf ..\..