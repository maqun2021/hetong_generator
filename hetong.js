/* --- CONFIGURATION --- */
// 定义各种表单元素的ID，方便统一管理
const ELEMENT_IDS = {
	kolType: 'kolType',
	signType: 'signType',
	fulfillmentTimeContainer: 'fulfillmentTimeContainer',
	fulfillmentTime: 'fulfillmentTime',
	datePickers: 'datePickers',
	datePicker_S: 'datePicker_S',
	datePicker_SM: 'datePicker_SM',
	datePicker_MD: 'datePicker_MD',
	datePicker_MM: 'datePicker_MM',
	normalVideoFields: 'normalVideoFields',
	videoCountField: 'videoCountField',
	releaseCountField: 'releaseCountField',
	kolHybridVideoFields: 'kolHybridVideoFields',
	strongCommercialCountField: 'strongCommercialCountField',
	strongCommercialReleaseCountField: 'strongCommercialReleaseCountField',
	pseudoNativeCountField: 'pseudoNativeCountField',
	pseudoNativeReleaseCountField: 'pseudoNativeReleaseCountField',
	// 其他需要引用的ID
	kolName: 'kolName',
	contentRetention: 'contentRetention',
	paymentMethod: 'paymentMethod',
	netTerm: 'netTerm',
	bonus: 'bonus',
	modifyCheck: 'modifyCheck',
	modifyTextContainer: 'modifyTextContainer',
	modifyText: 'modifyText',
	output: 'output',
	price: 'price',
	videoCount: 'videoCount',
	releaseCount: 'releaseCount',
	strongCommercialPrice: 'strongCommercialPrice',
	strongCommercialCount: 'strongCommercialCount',
	strongCommercialReleaseCount: 'strongCommercialReleaseCount',
	pseudoNativePrice: 'pseudoNativePrice',
	pseudoNativeCount: 'pseudoNativeCount',
	pseudoNativeReleaseCount: 'pseudoNativeReleaseCount',
	date_S: 'date_S',
	date_SM: 'date_SM',
	date_MD_start: 'date_MD_start',
	date_MD_end: 'date_MD_end',
	date_MM_start: 'date_MM_start',
	date_MM_end: 'date_MM_end',
	prepaymentField: 'prepaymentField',
	prepaymentPercent: 'prepaymentPercent',
	prepaymentDays: 'prepaymentDays'
};

// 定义履行时间的选项
const FULFILLMENT_TIME_OPTIONS = {
	MD: { value: 'MD', text: '日期区间' },
	S: { value: 'S', text: '具体日期' },
	MM: { value: 'MM', text: '月份区间' },
	SM: { value: 'SM', text: '具体月份' },
};

// 定义不同场景下的逻辑规则
const LOGIC_RULES = {
	KOC: {
		Y: { // 已履行
			timeOptions: ['S', 'MD'],
			fields: ['normalVideoFields', 'videoCountField', 'releaseCountField']
		},
		W: { // 未履行
			timeOptions: ['SM', 'MM'],
			fields: ['normalVideoFields', 'videoCountField']
		}
	},
	KOL: {
		Y: { // 已履行
			timeOptions: ['S', 'MD'],
			fields: ['normalVideoFields', 'videoCountField', 'releaseCountField']
		},
		W: { // 未履行
			timeOptions: ['S', 'SM', 'MD', 'MM'],
			fields: ['normalVideoFields', 'videoCountField']
		}
	},
	KOL_HYBRID: {
		Y: { // 已履行
			timeOptions: ['S', 'SM', 'MD', 'MM'],
			fields: ['kolHybridVideoFields', 'strongCommercialCountField', 'pseudoNativeCountField', 'strongCommercialReleaseCountField', 'pseudoNativeReleaseCountField']
		},
		W: { // 未履行
			timeOptions: ['S', 'SM', 'MD', 'MM'],
			fields: ['kolHybridVideoFields', 'strongCommercialCountField', 'pseudoNativeCountField']
		}
	}
};


/* --- CORE LOGIC --- */

/**
 * 主控制函数，根据合作类型和履行状态更新整个表单的可见性
 */
function updateFormVisibility() {
	const kolType = getEl(ELEMENT_IDS.kolType).value;
	const signType = getEl(ELEMENT_IDS.signType).value;
	const fulfillmentTime = getEl(ELEMENT_IDS.fulfillmentTime).value;

	// 0. 重置所有可能变化的字段
	resetAllFields();

	// 1. 检查是否满足显示条件
	if (!kolType || !signType) {
		return; // 如果合作类型或履行状态未选择，则不执行任何操作
	}

	const rule = LOGIC_RULES[kolType]?.[signType];
	if (!rule) return;

	// 2. 更新履行时间下拉框
	populateFulfillmentTimeOptions(rule.timeOptions);
	show(ELEMENT_IDS.fulfillmentTimeContainer);


	// 3. 如果履行时间已选择，则更新后续字段
	if (fulfillmentTime) {
		// a. 显示对应的日期选择器
		show(`datePicker_${fulfillmentTime}`);

		// b. 显示对应的价格和数量字段
		rule.fields.forEach(fieldId => {
			show(fieldId);
		});
	}
}

/**
 * 填充履行时间下拉框的选项
 * @param {string[]} options - 要显示的选项的key数组, e.g., ['S', 'MD']
 */
function populateFulfillmentTimeOptions(options) {
	const select = getEl(ELEMENT_IDS.fulfillmentTime);
	const currentVal = select.value;
	select.innerHTML = '<option value="">请选择时间类型</option>'; // 清空并添加默认选项

	// 按优先级顺序排序
	const priority = ['MD', 'S', 'MM', 'SM'];
	options
		.slice() // 复制一份
		.sort((a, b) => priority.indexOf(a) - priority.indexOf(b))
		.forEach(key => {
			const optionData = FULFILLMENT_TIME_OPTIONS[key];
			if (optionData) {
				const option = document.createElement('option');
				option.value = optionData.value;
				option.textContent = optionData.text;
				select.appendChild(option);
			}
		});

	// 尝试保留之前的选择
	if (options.includes(currentVal)) {
		select.value = currentVal;
	}
}


/**
 * 重置所有动态字段到初始隐藏状态
 */
function resetAllFields() {
	// 隐藏主容器
	hide(ELEMENT_IDS.fulfillmentTimeContainer);
	hide(ELEMENT_IDS.normalVideoFields);
	hide(ELEMENT_IDS.kolHybridVideoFields);

	// 隐藏所有日期选择器
	hide(ELEMENT_IDS.datePicker_S);
	hide(ELEMENT_IDS.datePicker_SM);
	hide(ELEMENT_IDS.datePicker_MD);
	hide(ELEMENT_IDS.datePicker_MM);

	// 隐藏所有数量字段
	hide(ELEMENT_IDS.videoCountField);
	hide(ELEMENT_IDS.releaseCountField);
	hide(ELEMENT_IDS.strongCommercialCountField);
	hide(ELEMENT_IDS.strongCommercialReleaseCountField);
	hide(ELEMENT_IDS.pseudoNativeCountField);
	hide(ELEMENT_IDS.pseudoNativeReleaseCountField);
}


/* --- TEXT GENERATION --- */

function generateText() {
	const kolType = getEl(ELEMENT_IDS.kolType).value;
	const signType = getEl(ELEMENT_IDS.signType).value;
	const fulfillmentTimeType = getEl(ELEMENT_IDS.fulfillmentTime).value;

	if (!kolType || !signType || !fulfillmentTimeType) {
		alert("请填写所有必填项！");
		return;
	}

	// 合作事项
	let text = "合作事项：\n";
	// 1. 标题
	if (kolType === 'KOL_HYBRID') {
		text += `1. 海外KOL强商单和伪原生合作（${getEl(ELEMENT_IDS.kolName).value}），发布平台${getCheckedPlatforms().replace(/, /g, ' & ')}。\n`;
	} else {
		text += `1. 海外${getEl(ELEMENT_IDS.kolType).options[getEl(ELEMENT_IDS.kolType).selectedIndex].text}（${getEl(ELEMENT_IDS.kolName).value}），发布平台${getCheckedPlatforms().replace(/, /g, ' & ')}。\n`;
	}

	// 2. 金额、签约支数、实际上线支数（仅已履行）、上线时间
	if (kolType === 'KOL_HYBRID') {
		text += `2. 强商单单支视频金额$${getEl(ELEMENT_IDS.strongCommercialPrice).value}，签约 ${getEl(ELEMENT_IDS.strongCommercialCount).value} 期`;
		if (signType === 'Y') {
			text += `，实际上线数量为 ${getEl(ELEMENT_IDS.strongCommercialReleaseCount).value} 支`;
		}
		text += `，伪原生视频单支视频金额$${getEl(ELEMENT_IDS.pseudoNativePrice).value}，签约 ${getEl(ELEMENT_IDS.pseudoNativeCount).value} 期`;
		if (signType === 'Y') {
			text += `，实际上线数量为 ${getEl(ELEMENT_IDS.pseudoNativeReleaseCount).value} 支`;
		}
		text += `，上线时间为 `;
		if (fulfillmentTimeType === 'S') {
			text += `${getEl(ELEMENT_IDS.date_S).value}。\n`;
		} else if (fulfillmentTimeType === 'SM') {
			text += `${getEl(ELEMENT_IDS.date_SM).value.replace('-', '年')}月。\n`;
		} else if (fulfillmentTimeType === 'MD') {
			text += `${getEl(ELEMENT_IDS.date_MD_start).value} 到 ${getEl(ELEMENT_IDS.date_MD_end).value}。\n`;
		} else if (fulfillmentTimeType === 'MM') {
			text += `${getEl(ELEMENT_IDS.date_MM_start).value.replace('-', '年')}月 - ${getEl(ELEMENT_IDS.date_MM_end).value.replace('-', '年')}月。\n`;
		}
	} else {
		text += `2. 单支视频金额$${getEl(ELEMENT_IDS.price).value}，签约 ${getEl(ELEMENT_IDS.videoCount).value} 期视频`;
		if (signType === 'Y') {
			text += `，实际上线视频数量为 ${getEl(ELEMENT_IDS.releaseCount).value} 支`;
		}
		if (fulfillmentTimeType === 'S') {
			text += `，视频上线时间为 ${getEl(ELEMENT_IDS.date_S).value}。`;
		} else if (fulfillmentTimeType === 'SM') {
			text += `，视频上线时间为 ${getEl(ELEMENT_IDS.date_SM).value.replace('-', '年')}月。`;
		} else if (fulfillmentTimeType === 'MD') {
			text += `，视频计划上线时间段为 ${getEl(ELEMENT_IDS.date_MD_start).value} - ${getEl(ELEMENT_IDS.date_MD_end).value}。`;
		} else if (fulfillmentTimeType === 'MM') {
			text += `，视频计划上线时间段为 ${getEl(ELEMENT_IDS.date_MM_start).value.replace('-', '年')}月 - ${getEl(ELEMENT_IDS.date_MM_end).value.replace('-', '年')}月。`;
		}
		text += "\n";
	}

	// 3. 奖励机制
	if (getEl(ELEMENT_IDS.bonus).value === '有') {
		text += "3. 有奖励机制，合同中有根据播放量制定的详细奖励机制，具体参见合同。\n";
	}

	// 权利义务
	text += "\n权利义务：(重点highlight)\n";
	text += `1. 未经甲方同意，乙方不得删除视频，内容${getEl(ELEMENT_IDS.contentRetention).value}保留，否则支付甲方50%的费用。\n`;
	text += "2. 乙方发布未经批准/错误版本视频，甲方可以选择补偿方式（删除重发、另行协商补偿、终止合作拒绝付款）。\n";

	// 付款条件
	text += "\n付款条件：\n";
	text += `${getEl(ELEMENT_IDS.paymentMethod).value}，视频上线后 ${getEl(ELEMENT_IDS.netTerm).value} days/video。`;

	// 修改条款
	if (getEl(ELEMENT_IDS.modifyCheck).checked) {
		text += `\n\n修改条款:\n${getEl(ELEMENT_IDS.modifyText).value}\n`;
	}

	getEl(ELEMENT_IDS.output).value = text;
}


/* --- HELPER FUNCTIONS --- */

// DOM element getters
function getEl(id) {
	return document.getElementById(id);
}

// Show/hide helpers
function show(elementOrId) {
	const el = (typeof elementOrId === 'string') ? getEl(elementOrId) : elementOrId;
	if (el) el.style.display = 'block';
}

function hide(elementOrId) {
	const el = (typeof elementOrId === 'string') ? getEl(elementOrId) : elementOrId;
	if (el) el.style.display = 'none';
}

function getCheckedPlatforms() {
	const checkboxes = document.querySelectorAll('input[name="platforms"]:checked');
	return Array.from(checkboxes).map(cb => cb.value).join(', ');
}

function generateNetTermText() {
	const netTerm = getEl(ELEMENT_IDS.netTerm).value;
	if (netTerm === 'prepayment') {
		const percent = getEl(ELEMENT_IDS.prepaymentPercent).value;
		const days = getEl(ELEMENT_IDS.prepaymentDays).value;
		return `预付 (视频批准后支付总额的${percent}%，发布${days}天后支付剩余部分)`;
	}
	return netTerm;
}

function copyToClipboard() {
	const output = getEl(ELEMENT_IDS.output);
	output.select();
	document.execCommand('copy');
	alert('已复制到剪贴板');
}

function toggleModifyText() {
	const container = getEl(ELEMENT_IDS.modifyTextContainer);
	container.style.display = getEl(ELEMENT_IDS.modifyCheck).checked ? "block" : "none";
}

function toggleNetFields() {
	const prepaymentField = getEl(ELEMENT_IDS.prepaymentField);
	prepaymentField.style.display = getEl(ELEMENT_IDS.netTerm).value === "prepayment" ? "block" : "none";
}

// Initial call to set up the form correctly on page load
document.addEventListener('DOMContentLoaded', () => {
	// It's better to reset the form on load
	getEl('kolType').value = '';
	getEl('signType').value = '';
	updateFormVisibility();
});
