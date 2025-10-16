WordCloudAPI[]:=
	APIFunction[{},
		Function[
			Enclose[
				Module[{data},
					data = ConfirmMatch[
						ImportString[HTTPRequestData["Body"],"RawJSON"],
						_List
						];
					Rasterize @ WordCloud[
						Flatten[	
							DeleteCases[
								data,
								{}
							]
						]
					] // HTTPResponse[
						ExportForm[#, "PNG"],
							<|
								"StatusCode" ->200,
								"ContentType" ->"image/png"
							|>
						]&
				],
				Function[e,
					HTTPResponse[
					ExportForm[
						<|
							"Success"->"False",
							"tag" -> e["Tag"],
							"message" -> e["Message"]
						
						|>
						, "RawJSON"],
					<|
						"StatusCode" ->500,
						"ContentType" ->"application/json"
					|>
					]
				]
			]
		]
	];

apiList = {
	{WordAPI[],			"WordCloudAPI"}
}

DeployAPI[]:=
	Enclose[
		MapApply[
			Function[{expr, loc},
				ConfirmMatch[
					CloudDeploy[expr, loc],
					_CloudObject
				]
			],
			apiList
		]
	]